/**
 * Script to add schema and pricing translations to all i18n files
 * Usage: node scripts/add-i18n-schema.js
 */

const fs = require('fs');
const path = require('path');

// Language-specific translations for schema and pricing
const translations = {
  de: { // German
    schema: {
      webApp: {
        name: "Word to Markdown Konverter",
        alternateName: "Word2MD",
        description: "Konvertieren Sie Word-Dokumente (.docx) mühelos in sauberes, strukturiertes Markdown. Schnell, sicher, keine Uploads erforderlich — läuft vollständig in Ihrem Browser.",
        features: [
          "Word zu Markdown konvertieren",
          "Stapelverarbeitung",
          "Keine Datei-Uploads erforderlich",
          "Browserbasierte Konvertierung",
          "Mehrsprachige Unterstützung",
          "ZIP-Download für mehrere Dateien"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Kostenloser Online-Word-to-Markdown-Konverter. Konvertieren Sie .docx-Dateien sofort im Browser ins Markdown-Format. Keine Uploads, völlig sicher und privat."
      },
      faq: [
        {
          question: "Ist Word2MD kostenlos nutzbar?",
          answer: "Ja, Word2MD ist völlig kostenlos nutzbar. Sie können unbegrenzt Word-Dokumente ohne Kosten oder Registrierung in Markdown konvertieren."
        },
        {
          question: "Laden Sie meine Dateien auf einen Server hoch?",
          answer: "Nein, alle Konvertierungen erfolgen direkt in Ihrem Browser. Ihre Dateien verlassen niemals Ihr Gerät, was vollständige Privatsphäre und Sicherheit gewährleistet."
        },
        {
          question: "Welche Word-Formate werden unterstützt?",
          answer: "Wir unterstützen .docx-Dateien (Microsoft Word 2007 und neuer). Legacy-.doc-Dateien werden derzeit nicht unterstützt."
        },
        {
          question: "Kann ich mehrere Dateien auf einmal konvertieren?",
          answer: "Ja, Sie können mehrere .docx-Dateien gleichzeitig hochladen und konvertieren. Alle konvertierten Dateien können als einzelne Markdown-Dateien heruntergeladen oder in einem ZIP-Archiv gepackt werden."
        },
        {
          question: "Welche Markdown-Funktionen werden unterstützt?",
          answer: "Wir unterstützen die Standard-Markdown-Syntax einschließlich Überschriften, Listen, Links, Bildern, Tabellen, Fettdruck, Kursivschrift, Codeblöcken und mehr. Die Konvertierung erhält Dokumentstruktur und Formatierung so weit wie möglich."
        }
      ]
    },
    pricing: {
      cnPay: "Mit CNY bezahlen 👉"
    }
  },
  es: { // Spanish
    schema: {
      webApp: {
        name: "Conversor de Word a Markdown",
        alternateName: "Word2MD",
        description: "Convierte documentos de Word (.docx) a Markdown limpio y estructurado sin esfuerzo. Rápido, seguro, sin cargas requeridas — se ejecuta completamente en tu navegador.",
        features: [
          "Convertir Word a Markdown",
          "Procesamiento por lotes",
          "No requiere cargar archivos",
          "Conversión basada en navegador",
          "Soporte multiidioma",
          "Descarga ZIP para múltiples archivos"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Conversor gratuito en línea de Word a Markdown. Convierte archivos .docx a formato Markdown instantáneamente en tu navegador. Sin cargas, completamente seguro y privado."
      },
      faq: [
        {
          question: "¿Word2MD es gratuito?",
          answer: "Sí, Word2MD es completamente gratuito. Puedes convertir documentos de Word ilimitados a Markdown sin costo ni registro."
        },
        {
          question: "¿Suben mis archivos a un servidor?",
          answer: "No, todas las conversiones ocurren directamente en tu navegador. Tus archivos nunca salen de tu dispositivo, asegurando privacidad y seguridad completa."
        },
        {
          question: "¿Qué formatos de Word se admiten?",
          answer: "Admitimos archivos .docx (Microsoft Word 2007 y posteriores). Los archivos .doc antiguos no están soportados actualmente."
        },
        {
          question: "¿Puedo convertir varios archivos a la vez?",
          answer: "Sí, puedes cargar y convertir varios archivos .docx simultáneamente. Todos los archivos convertidos se pueden descargar como archivos Markdown individuales o empaquetados en un archivo ZIP."
        },
        {
          question: "¿Qué características de Markdown se admiten?",
          answer: "Admitimos la sintaxis estándar de Markdown, incluidos encabezados, listas, enlaces, imágenes, tablas, negrita, cursiva, bloques de código y más. La conversión preserva la estructura y el formato del documento lo más posible."
        }
      ]
    },
    pricing: {
      cnPay: "Pagar con CNY 👉"
    }
  },
  fr: { // French
    schema: {
      webApp: {
        name: "Convertisseur Word vers Markdown",
        alternateName: "Word2MD",
        description: "Convertissez facilement des documents Word (.docx) en Markdown propre et structuré. Rapide, sécurisé, aucun téléchargement requis — fonctionne entièrement dans votre navigateur.",
        features: [
          "Convertir Word en Markdown",
          "Traitement par lots",
          "Aucun téléchargement de fichier requis",
          "Conversion dans le navigateur",
          "Support multilingue",
          "Téléchargement ZIP pour plusieurs fichiers"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Convertisseur gratuit en ligne Word vers Markdown. Convertissez instantanément des fichiers .docx au format Markdown dans votre navigateur. Aucun téléchargement, totalement sécurisé et privé."
      },
      faq: [
        {
          question: "Word2MD est-il gratuit?",
          answer: "Oui, Word2MD est totalement gratuit. Vous pouvez convertir un nombre illimité de documents Word en Markdown sans frais ni inscription."
        },
        {
          question: "Téléchargez-vous mes fichiers sur un serveur?",
          answer: "Non, toutes les conversions se font directement dans votre navigateur. Vos fichiers ne quittent jamais votre appareil, garantissant une confidentialité et une sécurité totales."
        },
        {
          question: "Quels formats Word sont pris en charge?",
          answer: "Nous prenons en charge les fichiers .docx (Microsoft Word 2007 et ultérieur). Les anciens fichiers .doc ne sont pas pris en charge actuellement."
        },
        {
          question: "Puis-je convertir plusieurs fichiers à la fois?",
          answer: "Oui, vous pouvez télécharger et convertir plusieurs fichiers .docx simultanément. Tous les fichiers convertis peuvent être téléchargés en tant que fichiers Markdown individuels ou emballés dans une archive ZIP."
        },
        {
          question: "Quelles fonctionnalités Markdown sont prises en charge?",
          answer: "Nous prenons en charge la syntaxe Markdown standard, y compris les titres, listes, liens, images, tableaux, gras, italique, blocs de code et plus. La conversion préserve la structure et le formatage du document autant que possible."
        }
      ]
    },
    pricing: {
      cnPay: "Payer avec CNY 👉"
    }
  },
  it: { // Italian
    schema: {
      webApp: {
        name: "Convertitore da Word a Markdown",
        alternateName: "Word2MD",
        description: "Converti facilmente documenti Word (.docx) in Markdown pulito e strutturato. Veloce, sicuro, nessun caricamento richiesto — funziona interamente nel tuo browser.",
        features: [
          "Converti Word in Markdown",
          "Elaborazione batch",
          "Nessun caricamento file richiesto",
          "Conversione basata su browser",
          "Supporto multilingue",
          "Download ZIP per più file"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Convertitore gratuito online da Word a Markdown. Converti istantaneamente file .docx in formato Markdown nel tuo browser. Nessun caricamento, completamente sicuro e privato."
      },
      faq: [
        {
          question: "Word2MD è gratuito?",
          answer: "Sì, Word2MD è completamente gratuito. Puoi convertire documenti Word illimitati in Markdown senza costi o registrazione."
        },
        {
          question: "Caricate i miei file su un server?",
          answer: "No, tutte le conversioni avvengono direttamente nel tuo browser. I tuoi file non lasciano mai il tuo dispositivo, garantendo privacy e sicurezza complete."
        },
        {
          question: "Quali formati Word sono supportati?",
          answer: "Supportiamo file .docx (Microsoft Word 2007 e successivi). I file .doc legacy non sono attualmente supportati."
        },
        {
          question: "Posso convertire più file contemporaneamente?",
          answer: "Sì, puoi caricare e convertire più file .docx simultaneamente. Tutti i file convertiti possono essere scaricati come singoli file Markdown o impacchettati in un archivio ZIP."
        },
        {
          question: "Quali funzionalità Markdown sono supportate?",
          answer: "Supportiamo la sintassi Markdown standard, inclusi titoli, elenchi, link, immagini, tabelle, grassetto, corsivo, blocchi di codice e altro. La conversione preserva struttura e formattazione del documento il più possibile."
        }
      ]
    },
    pricing: {
      cnPay: "Paga con CNY 👉"
    }
  },
  pt: { // Portuguese
    schema: {
      webApp: {
        name: "Conversor de Word para Markdown",
        alternateName: "Word2MD",
        description: "Converta documentos Word (.docx) para Markdown limpo e estruturado sem esforço. Rápido, seguro, sem uploads necessários — executa totalmente no seu navegador.",
        features: [
          "Converter Word para Markdown",
          "Processamento em lote",
          "Nenhum upload de arquivo necessário",
          "Conversão baseada em navegador",
          "Suporte multilíngue",
          "Download ZIP para vários arquivos"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Conversor gratuito online de Word para Markdown. Converta arquivos .docx para o formato Markdown instantaneamente no seu navegador. Sem uploads, completamente seguro e privado."
      },
      faq: [
        {
          question: "O Word2MD é gratuito?",
          answer: "Sim, o Word2MD é completamente gratuito. Você pode converter documentos Word ilimitados para Markdown sem custos ou registro."
        },
        {
          question: "Vocês enviam meus arquivos para um servidor?",
          answer: "Não, todas as conversões acontecem diretamente no seu navegador. Seus arquivos nunca saem do seu dispositivo, garantindo privacidade e segurança completas."
        },
        {
          question: "Quais formatos Word são suportados?",
          answer: "Suportamos arquivos .docx (Microsoft Word 2007 e posteriores). Arquivos .doc legados não são suportados atualmente."
        },
        {
          question: "Posso converter vários arquivos de uma vez?",
          answer: "Sim, você pode enviar e converter vários arquivos .docx simultaneamente. Todos os arquivos convertidos podem ser baixados como arquivos Markdown individuais ou empacotados em um arquivo ZIP."
        },
        {
          question: "Quais recursos Markdown são suportados?",
          answer: "Suportamos sintaxe Markdown padrão, incluindo títulos, listas, links, imagens, tabelas, negrito, itálico, blocos de código e mais. A conversão preserva estrutura e formatação do documento o máximo possível."
        }
      ]
    },
    pricing: {
      cnPay: "Pagar com CNY 👉"
    }
  },
  ru: { // Russian
    schema: {
      webApp: {
        name: "Конвертер Word в Markdown",
        alternateName: "Word2MD",
        description: "Легко конвертируйте документы Word (.docx) в чистый структурированный Markdown. Быстро, безопасно, без загрузок — работает полностью в вашем браузере.",
        features: [
          "Конвертация Word в Markdown",
          "Пакетная обработка",
          "Не требуется загрузка файлов",
          "Конвертация в браузере",
          "Многоязычная поддержка",
          "ZIP-загрузка для нескольких файлов"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Бесплатный онлайн-конвертер Word в Markdown. Мгновенно конвертируйте файлы .docx в формат Markdown в браузере. Без загрузок, полностью безопасно и приватно."
      },
      faq: [
        {
          question: "Word2MD бесплатен?",
          answer: "Да, Word2MD полностью бесплатен. Вы можете конвертировать неограниченное количество документов Word в Markdown без стоимости или регистрации."
        },
        {
          question: "Загружаете ли вы мои файлы на сервер?",
          answer: "Нет, вся конвертация происходит непосредственно в вашем браузере. Ваши файлы никогда не покидают ваше устройство, обеспечивая полную конфиденциальность и безопасность."
        },
        {
          question: "Какие форматы Word поддерживаются?",
          answer: "Мы поддерживаем файлы .docx (Microsoft Word 2007 и более поздние). Устаревшие файлы .doc в настоящее время не поддерживаются."
        },
        {
          question: "Могу ли я конвертировать несколько файлов одновременно?",
          answer: "Да, вы можете загрузить и конвертировать несколько файлов .docx одновременно. Все конвертированные файлы могут быть загружены как отдельные файлы Markdown или упакованы в ZIP-архив."
        },
        {
          question: "Какие функции Markdown поддерживаются?",
          answer: "Мы поддерживаем стандартный синтаксис Markdown, включая заголовки, списки, ссылки, изображения, таблицы, жирный шрифт, курсив, блоки кода и многое другое. Конвертация сохраняет структуру и форматирование документа максимально возможно."
        }
      ]
    },
    pricing: {
      cnPay: "Оплатить в CNY 👉"
    }
  },
  ar: { // Arabic
    schema: {
      webApp: {
        name: "محول Word إلى Markdown",
        alternateName: "Word2MD",
        description: "حول مستندات Word (.docx) بسهولة إلى Markdown نظيف ومنظم. سريع وآمن، لا يتطلب تحميلات — يعمل بالكامل في متصفحك.",
        features: [
          "تحويل Word إلى Markdown",
          "معالجة دفعية",
          "لا يتطلب تحميل ملفات",
          "تحويل قائم على المتصفح",
          "دعم متعدد اللغات",
          "تنزيل ZIP لملفات متعددة"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "محول مجاني عبر الإنترنت من Word إلى Markdown. حول ملفات .docx إلى تنسيق Markdown فوراً في متصفحك. بدون تحميلات، آمن وخاص تماماً."
      },
      faq: [
        {
          question: "هل Word2MD مجاني؟",
          answer: "نعم، Word2MD مجاني تماماً. يمكنك تحويل مستندات Word غير محدودة إلى Markdown بدون تكلفة أو تسجيل."
        },
        {
          question: "هل تقومون بتحميل ملفاتي إلى خادم?",
          answer: "لا، جميع التحويلات تحدث مباشرة في متصفحك. ملفاتك لا تغادر جهازك أبداً، مما يضمن خصوصية وأمان كاملين."
        },
        {
          question: "ما هي صيغ Word المدعومة؟",
          answer: "ندعم ملفات .docx (Microsoft Word 2007 والإصدارات الأحدث). ملفات .doc القديمة غير مدعومة حالياً."
        },
        {
          question: "هل يمكنني تحويل عدة ملفات في وقت واحد؟",
          answer: "نعم، يمكنك تحميل وتحويل عدة ملفات .docx في وقت واحد. يمكن تنزيل جميع الملفات المحولة كملفات Markdown فردية أو معبأة في أرشيف ZIP."
        },
        {
          question: "ما هي ميزات Markdown المدعومة؟",
          answer: "ندعم بناء جملة Markdown القياسي بما في ذلك العناوين والقوائم والروابط والصور والجداول والنص الغامق والمائل وكتل الكود والمزيد. يحافظ التحويل على بنية المستند وتنسيقه قدر الإمكان."
        }
      ]
    },
    pricing: {
      cnPay: "الدفع باليوان 👉"
    }
  },
  vi: { // Vietnamese
    schema: {
      webApp: {
        name: "Trình chuyển đổi Word sang Markdown",
        alternateName: "Word2MD",
        description: "Chuyển đổi tài liệu Word (.docx) sang Markdown sạch và có cấu trúc một cách dễ dàng. Nhanh, an toàn, không cần tải lên — chạy hoàn toàn trong trình duyệt của bạn.",
        features: [
          "Chuyển đổi Word sang Markdown",
          "Xử lý hàng loạt",
          "Không cần tải tập tin lên",
          "Chuyển đổi dựa trên trình duyệt",
          "Hỗ trợ đa ngôn ngữ",
          "Tải xuống ZIP cho nhiều tập tin"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Trình chuyển đổi Word sang Markdown trực tuyến miễn phí. Chuyển đổi tập tin .docx sang định dạng Markdown ngay lập tức trong trình duyệt. Không tải lên, hoàn toàn an toàn và riêng tư."
      },
      faq: [
        {
          question: "Word2MD có miễn phí không?",
          answer: "Có, Word2MD hoàn toàn miễn phí. Bạn có thể chuyển đổi không giới hạn tài liệu Word sang Markdown mà không mất phí hoặc đăng ký."
        },
        {
          question: "Bạn có tải tập tin của tôi lên máy chủ không?",
          answer: "Không, tất cả các chuyển đổi diễn ra trực tiếp trong trình duyệt của bạn. Tập tin của bạn không bao giờ rời khỏi thiết bị, đảm bảo quyền riêng tư và bảo mật hoàn toàn."
        },
        {
          question: "Định dạng Word nào được hỗ trợ?",
          answer: "Chúng tôi hỗ trợ tập tin .docx (Microsoft Word 2007 trở lên). Tập tin .doc cũ hiện không được hỗ trợ."
        },
        {
          question: "Tôi có thể chuyển đổi nhiều tập tin cùng lúc không?",
          answer: "Có, bạn có thể tải lên và chuyển đổi nhiều tập tin .docx đồng thời. Tất cả tập tin đã chuyển đổi có thể được tải xuống dưới dạng tập tin Markdown riêng lẻ hoặc đóng gói trong kho lưu trữ ZIP."
        },
        {
          question: "Những tính năng Markdown nào được hỗ trợ?",
          answer: "Chúng tôi hỗ trợ cú pháp Markdown tiêu chuẩn bao gồm tiêu đề, danh sách, liên kết, hình ảnh, bảng, in đậm, in nghiêng, khối mã và nhiều hơn nữa. Chuyển đổi bảo toàn cấu trúc và định dạng tài liệu càng nhiều càng tốt."
        }
      ]
    },
    pricing: {
      cnPay: "Thanh toán bằng CNY 👉"
    }
  },
  hi: { // Hindi
    schema: {
      webApp: {
        name: "Word से Markdown कन्वर्टर",
        alternateName: "Word2MD",
        description: "Word दस्तावेज़ों (.docx) को सहजता से स्वच्छ, संरचित Markdown में परिवर्तित करें। तेज़, सुरक्षित, कोई अपलोड आवश्यक नहीं — पूरी तरह से आपके ब्राउज़र में चलता है।",
        features: [
          "Word को Markdown में बदलें",
          "बैच फ़ाइल प्रोसेसिंग",
          "कोई फ़ाइल अपलोड आवश्यक नहीं",
          "ब्राउज़र-आधारित रूपांतरण",
          "बहुभाषी समर्थन",
          "एकाधिक फ़ाइलों के लिए ZIP डाउनलोड"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "निःशुल्क ऑनलाइन Word से Markdown कन्वर्टर। अपने ब्राउज़र में तुरंत .docx फ़ाइलों को Markdown प्रारूप में बदलें। कोई अपलोड नहीं, पूरी तरह से सुरक्षित और निजी।"
      },
      faq: [
        {
          question: "क्या Word2MD मुफ़्त है?",
          answer: "हां, Word2MD पूरी तरह से मुफ़्त है। आप बिना किसी लागत या पंजीकरण के असीमित Word दस्तावेज़ों को Markdown में परिवर्तित कर सकते हैं।"
        },
        {
          question: "क्या आप मेरी फ़ाइलें सर्वर पर अपलोड करते हैं?",
          answer: "नहीं, सभी रूपांतरण सीधे आपके ब्राउज़र में होते हैं। आपकी फ़ाइलें कभी भी आपके डिवाइस को नहीं छोड़तीं, पूर्ण गोपनीयता और सुरक्षा सुनिश्चित करती हैं।"
        },
        {
          question: "कौन से Word प्रारूप समर्थित हैं?",
          answer: "हम .docx फ़ाइलों (Microsoft Word 2007 और बाद के संस्करण) का समर्थन करते हैं। पुराने .doc फ़ाइलें वर्तमान में समर्थित नहीं हैं।"
        },
        {
          question: "क्या मैं एक बार में कई फ़ाइलें परिवर्तित कर सकता हूं?",
          answer: "हां, आप एक साथ कई .docx फ़ाइलें अपलोड और परिवर्तित कर सकते हैं। सभी परिवर्तित फ़ाइलों को व्यक्तिगत Markdown फ़ाइलों के रूप में डाउनलोड किया जा सकता है या ZIP संग्रह में पैक किया जा सकता है।"
        },
        {
          question: "कौन सी Markdown सुविधाएं समर्थित हैं?",
          answer: "हम मानक Markdown सिंटैक्स का समर्थन करते हैं जिसमें शीर्षक, सूचियां, लिंक, चित्र, तालिकाएं, बोल्ड, इटैलिक, कोड ब्लॉक और अधिक शामिल हैं। रूपांतरण दस्तावेज़ संरचना और स्वरूपण को यथासंभव संरक्षित करता है।"
        }
      ]
    },
    pricing: {
      cnPay: "CNY में भुगतान करें 👉"
    }
  },
  id: { // Indonesian
    schema: {
      webApp: {
        name: "Konverter Word ke Markdown",
        alternateName: "Word2MD",
        description: "Konversi dokumen Word (.docx) ke Markdown yang bersih dan terstruktur dengan mudah. Cepat, aman, tidak perlu unggah — berjalan sepenuhnya di browser Anda.",
        features: [
          "Konversi Word ke Markdown",
          "Pemrosesan file batch",
          "Tidak perlu mengunggah file",
          "Konversi berbasis browser",
          "Dukungan multi-bahasa",
          "Unduhan ZIP untuk banyak file"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "Konverter Word ke Markdown online gratis. Konversi file .docx ke format Markdown secara instan di browser Anda. Tanpa unggahan, sepenuhnya aman dan privat."
      },
      faq: [
        {
          question: "Apakah Word2MD gratis?",
          answer: "Ya, Word2MD sepenuhnya gratis. Anda dapat mengkonversi dokumen Word tanpa batas ke Markdown tanpa biaya atau pendaftaran."
        },
        {
          question: "Apakah Anda mengunggah file saya ke server?",
          answer: "Tidak, semua konversi terjadi langsung di browser Anda. File Anda tidak pernah meninggalkan perangkat Anda, memastikan privasi dan keamanan lengkap."
        },
        {
          question: "Format Word apa yang didukung?",
          answer: "Kami mendukung file .docx (Microsoft Word 2007 dan yang lebih baru). File .doc lama saat ini tidak didukung."
        },
        {
          question: "Bisakah saya mengkonversi beberapa file sekaligus?",
          answer: "Ya, Anda dapat mengunggah dan mengkonversi beberapa file .docx secara bersamaan. Semua file yang dikonversi dapat diunduh sebagai file Markdown individual atau dikemas dalam arsip ZIP."
        },
        {
          question: "Fitur Markdown apa yang didukung?",
          answer: "Kami mendukung sintaks Markdown standar termasuk heading, list, link, gambar, tabel, bold, italic, blok kode, dan banyak lagi. Konversi mempertahankan struktur dan format dokumen semaksimal mungkin."
        }
      ]
    },
    pricing: {
      cnPay: "Bayar dengan CNY 👉"
    }
  },
  th: { // Thai
    schema: {
      webApp: {
        name: "ตัวแปลง Word เป็น Markdown",
        alternateName: "Word2MD",
        description: "แปลงเอกสาร Word (.docx) เป็น Markdown ที่สะอาดและมีโครงสร้างได้อย่างง่ายดาย รวดเร็ว ปลอดภัย ไม่ต้องอัปโหลด — ทำงานทั้งหมดในเบราว์เซอร์ของคุณ",
        features: [
          "แปลง Word เป็น Markdown",
          "ประมวลผลไฟล์แบบกลุ่ม",
          "ไม่ต้องอัปโหลดไฟล์",
          "การแปลงบนเบราว์เซอร์",
          "รองรับหลายภาษา",
          "ดาวน์โหลด ZIP สำหรับหลายไฟล์"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "ตัวแปลง Word เป็น Markdown ออนไลน์ฟรี แปลงไฟล์ .docx เป็นรูปแบบ Markdown ทันทีในเบราว์เซอร์ของคุณ ไม่ต้องอัปโหลด ปลอดภัยและเป็นส่วนตัวอย่างสมบูรณ์"
      },
      faq: [
        {
          question: "Word2MD ฟรีหรือไม่?",
          answer: "ใช่ Word2MD ฟรีอย่างสมบูรณ์ คุณสามารถแปลงเอกสาร Word ได้ไม่จำกัดเป็น Markdown โดยไม่มีค่าใช้จ่ายหรือการลงทะเบียน"
        },
        {
          question: "คุณอัปโหลดไฟล์ของฉันไปยังเซิร์ฟเวอร์หรือไม่?",
          answer: "ไม่ การแปลงทั้งหมดเกิดขึ้นโดยตรงในเบราว์เซอร์ของคุณ ไฟล์ของคุณจะไม่ออกจากอุปกรณ์ของคุณเลย รับประกันความเป็นส่วนตัวและความปลอดภัยอย่างสมบูรณ์"
        },
        {
          question: "รองรับรูปแบบ Word อะไรบ้าง?",
          answer: "เรารองรับไฟล์ .docx (Microsoft Word 2007 และใหม่กว่า) ไฟล์ .doc รุ่นเก่าไม่รองรับในขณะนี้"
        },
        {
          question: "ฉันสามารถแปลงหลายไฟล์พร้อมกันได้หรือไม่?",
          answer: "ได้ คุณสามารถอัปโหลดและแปลงไฟล์ .docx หลายไฟล์พร้อมกันได้ ไฟล์ที่แปลงทั้งหมดสามารถดาวน์โหลดเป็นไฟล์ Markdown แยกกันหรือบรรจุในไฟล์ ZIP"
        },
        {
          question: "รองรับฟีเจอร์ Markdown อะไรบ้าง?",
          answer: "เรารองรับไวยากรณ์ Markdown มาตรฐาน รวมถึงหัวข้อ รายการ ลิงก์ รูปภาพ ตาราง ตัวหนา ตัวเอียง บล็อกโค้ด และอื่นๆ การแปลงจะรักษาโครงสร้างและการจัดรูปแบบเอกสารให้มากที่สุดเท่าที่เป็นไปได้"
        }
      ]
    },
    pricing: {
      cnPay: "ชำระเงินด้วย CNY 👉"
    }
  },
  "zh-hk": { // Traditional Chinese (Hong Kong)
    schema: {
      webApp: {
        name: "Word 轉 Markdown 轉換器",
        alternateName: "Word2MD",
        description: "輕鬆將 Word 文檔 (.docx) 轉換為整潔、結構化的 Markdown。快速、安全、無需上傳——完全在您的瀏覽器中運行。",
        features: [
          "Word 轉 Markdown",
          "批次檔案處理",
          "無需上傳檔案",
          "基於瀏覽器的轉換",
          "多語言支援",
          "多檔案 ZIP 下載"
        ]
      },
      organization: {
        name: "Word2MD",
        description: "免費線上 Word 轉 Markdown 轉換器。在瀏覽器中即時將 .docx 檔案轉換為 Markdown 格式。無需上傳，完全安全和私密。"
      },
      faq: [
        {
          question: "Word2MD 是免費的嗎?",
          answer: "是的，Word2MD 完全免費使用。您可以無限制地將 Word 文檔轉換為 Markdown，無需任何費用或註冊。"
        },
        {
          question: "你們會上傳我的檔案到伺服器嗎?",
          answer: "不會，所有轉換都在您的瀏覽器中直接進行。您的檔案永遠不會離開您的裝置，確保完全的隱私和安全。"
        },
        {
          question: "支援哪些 Word 格式?",
          answer: "我們支援 .docx 檔案（Microsoft Word 2007 及更高版本）。目前不支援舊版 .doc 檔案。"
        },
        {
          question: "可以一次轉換多個檔案嗎?",
          answer: "可以，您可以同時上傳和轉換多個 .docx 檔案。所有轉換後的檔案可以作為單獨的 Markdown 檔案下載，或打包在 ZIP 存檔中。"
        },
        {
          question: "支援哪些 Markdown 功能?",
          answer: "我們支援標準 Markdown 語法，包括標題、列表、連結、圖片、表格、粗體、斜體、程式碼區塊等。轉換會盡可能保留文檔結構和格式。"
        }
      ]
    },
    pricing: {
      cnPay: "人民幣支付 👉"
    }
  }
};

// Function to add schema and pricing to a language file
function addSchemaToLanguage(locale) {
  const filePath = path.join(__dirname, `../i18n/messages/${locale}.json`);

  try {
    // Read existing file
    const content = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(content);

    // Check if schema and pricing already exist
    if (data.schema && data.pricing) {
      console.log(`✓ ${locale}.json already has schema and pricing`);
      return;
    }

    // Add schema and pricing
    data.schema = translations[locale].schema;
    data.pricing = translations[locale].pricing;

    // Write back to file with pretty formatting
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
    console.log(`✓ Added schema and pricing to ${locale}.json`);
  } catch (error) {
    console.error(`✗ Error processing ${locale}.json:`, error.message);
  }
}

// Main execution
console.log('🚀 Adding schema and pricing translations to i18n files\n');

// Languages to process (excluding already done: en, zh, ja, ko)
const languagesToProcess = ['de', 'es', 'fr', 'it', 'pt', 'ru', 'ar', 'vi', 'hi', 'id', 'th', 'zh-hk'];

languagesToProcess.forEach(locale => {
  addSchemaToLanguage(locale);
});

console.log('\n✅ All translations added successfully!');
console.log('\nSummary:');
console.log('- Already completed: en, zh, ja, ko');
console.log('- Just added:', languagesToProcess.join(', '));
console.log('- Total: 16 languages');
